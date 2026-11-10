      program test_pdf
      implicit none
      double precision x, q, pdf(-6:7)
      integer i
      double precision xs(8)
      data xs /1d-4,1d-3,1d-2,5d-2,1d-1,2d-1,4d-1,8d-1/
      call NNPDFDriver('NNPDF23_lo_as_0130_qed_mem0.grid')
      call NNinitPDF(0)
      q = 91.188d0
      do i=1,8
         x = xs(i)
         call NNevolvePDF(x,q,pdf)
         write(*,*) x, pdf(0), pdf(2), pdf(-2), pdf(1), pdf(-1), pdf(4), pdf(-4)
      enddo
      end

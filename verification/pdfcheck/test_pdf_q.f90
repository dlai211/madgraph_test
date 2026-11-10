program test_pdf_q
  implicit none
  double precision x, q, pdf(-6:7)
  double precision qs(3)
  integer i,j
  data qs /9.55d0, 91.188d0, 8315.d0/
  call NNPDFDriver('NNPDF23_lo_as_0130_qed_mem0.grid')
  call NNinitPDF(0)
  x = 0.1d0
  do j=1,3
     q = qs(j)
     call NNevolvePDF(x,q,pdf)
     write(*,*) q, pdf(0), pdf(2), pdf(-2), pdf(1), pdf(-1)
  enddo
end
